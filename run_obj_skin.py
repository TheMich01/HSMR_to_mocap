from lib.kits.hsmr_demo import *
from pathlib import Path
import numpy as np

def save_mesh_as_obj(vertices, faces, output_path):
    """Salva una mesh in formato .obj senza usare librerie esterne."""
    print(f"Saving mesh to {output_path}")
    with open(output_path, "w") as f:
        # Scrivi i vertici
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        # Scrivi le facce (indici da 1)
        if faces is not None:
            for face in faces:
                f.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")
        else:
            print(f"No faces provided for {output_path}")

def main():
    # ⛩️ 0. Preparation.
    args = parse_args()
    outputs_root = Path(args.output_path) if args.output_path else Path("data_outputs/demos")
    outputs_root.mkdir(parents=True, exist_ok=True)
    mesh_output_dir = outputs_root / "meshes"
    mesh_output_dir.mkdir(exist_ok=True)

    monitor = TimeMonitor()

    # ⛩️ 1. Preprocess.
    with monitor('Data Preprocessing'):
        with monitor('Load Inputs'):
            print("Loading inputs...")
            raw_imgs, inputs_meta = load_inputs(args)

        with monitor('Detector Initialization'):
            get_logger(brief=True).info('🧱 Building detector.')
            detector = build_detector(
                    batch_size   = args.det_bs,
                    max_img_size = args.det_mis,
                    device       = args.device,
                )

        with monitor('Detecting'):
            get_logger(brief=True).info(f'🖼️ Detecting...')
            detector_outputs = detector(raw_imgs)

        with monitor('Patching & Loading'):
            patches, det_meta = imgs_det2patches(raw_imgs, *detector_outputs, args.max_instances)
        if len(patches) == 0:
            get_logger(brief=True).error(f'🚫 No human instance detected. Please ensure the validity of your inputs!')
        get_logger(brief=True).info(f'🔍 Totally {len(patches)} human instances are detected.')

    # ⛩️ 2. Human skeleton and mesh recovery (solo skin).
    with monitor('Pipeline Initialization'):
        get_logger(brief=True).info(f'🧱 Building recovery pipeline.')
        pipeline = build_inference_pipeline(model_root=args.model_root, device=args.device)

    with monitor('Recovery'):
        get_logger(brief=True).info(f'🏃 Recovering with B={args.rec_bs}...')
        pd_params, pd_cam_t = [], []
        for bw in asb(total=len(patches), bs_scope=args.rec_bs, enable_tqdm=True):
            patches_i = np.concatenate(patches[bw.sid:bw.eid], axis=0)
            patches_normalized_i = (patches_i - IMG_MEAN_255) / IMG_STD_255
            patches_normalized_i = patches_normalized_i.transpose(0, 3, 1, 2)
            with torch.no_grad():
                outputs = pipeline(patches_normalized_i)
            pd_params.append({k: v.detach().cpu().clone() for k, v in outputs['pd_params'].items()})
            pd_cam_t.append(outputs['pd_cam_t'].detach().cpu().clone())

        pd_params = assemble_dict(pd_params, expand_dim=False)
        pd_cam_t = torch.cat(pd_cam_t, dim=0)
        dump_results = {
                'patch_cam_t' : pd_cam_t.numpy(),
                **{k: v.numpy() for k, v in pd_params.items()},
            }

        get_logger(brief=True).info(f'🤌 Preparing skin meshes...')
        m_skin, _ = prepare_mesh(pipeline, pd_params)  # Ignora m_skel
        get_logger(brief=True).info(f'🏁 Done.')

    # ⛩️ 3. Postprocess (solo skin).
    with monitor('Visualization'):
        results, full_cam_t = visualize_full_img(pd_cam_t, raw_imgs, det_meta, m_skin, None, args.have_caption)  # Nessun m_skel
        dump_results['full_cam_t'] = full_cam_t

        # Debug: stampa il formato di m_skin
        print(f"m_skin type: {type(m_skin)}")
        print(f"m_skin keys: {list(m_skin.keys())}")
        print(f"m_skin['v'] shape: {m_skin['v'].shape}")

        # Salva solo le mesh della skin come .obj
        get_logger(brief=True).info(f'💾 Saving skin meshes as .obj...')
        for i in range(m_skin['v'].shape[0]):
            save_mesh_as_obj(m_skin['v'][i], m_skin['f'], mesh_output_dir / f"skin_frame_{i:03d}.obj")

        # Save rendering and dump results.
        if inputs_meta['type'] == 'video':
            seq_name = f'{pipeline.name}-' + inputs_meta['seq_name']
            save_video(results, outputs_root / f'{seq_name}.mp4')
            np.savez(outputs_root / f'{seq_name}.npz', **dump_results)
        elif inputs_meta['type'] == 'imgs':
            img_names = [f'{pipeline.name}-{fn.name}' for fn in inputs_meta['img_fns']]
            dump_results = disassemble_dict(dump_results, keep_dim=True)
            for i, img_name in enumerate(tqdm(img_names, desc='Saving images')):
                save_img(results[i], outputs_root / f'{img_name}.jpg')
                np.savez(outputs_root / f'{img_name}.npz', **dump_results[i])

        get_logger(brief=True).info(f'🎨 Rendering results and skin meshes are under {outputs_root}.')

    get_logger(brief=True).info(f'🎊 Everything is done!')
    monitor.report()

if __name__ == '__main__':
    main()
