# Reconstructing Humans motion extracting data from HSMR

> [**Original HSMR Repo - Reconstructing Humans with a Biomechanically Accurate Skeleton**](https://github.com/IsshikiHugh/HSMR)
> <br>
> <br>
> *CVPR 2025 (Oral)*


## 📢 News

- [2025.04.12] HSMR to mocap process has been released 2025! 🎉

## ⚒️ Setup

Install [HSMR](https://github.com/IsshikiHugh/HSMR) locally on your computer from the original repo, then copy the run_obj_skin.py file of this repo inside the exp folder of your HSMR local environment, and use it instead of the original one, then follow the guide below.
It starts with extraction of meshes from the video in a very shor time.
Then using 3DS Max with the script available in this repo you can convert the obj sequence in animation markers that can be used to guide any 3D character with any software.
The process continue inside Motion Builder where the markers are used to drive an actor an then retarget to another character.
Now the process can be automated, with just few step any video can be used to creata a tracking data that can be directly loaded to the actor created.
What is unique in this mocap sistem: there is NO need to make any calibration for the motion capture, anyone can use any video files, like a movie sceene, to extract motion capture data that can be applyed to any 3D character.

## 🚀 Demo & Quick Start

<!--
**[<img src="https://i.imgur.com/QCojoJk.png" width="30"> Google Colab demo](#) |
[<img src="https://s2.loli.net/2024/09/15/aw3rElfQAsOkNCn.png" width="20"> HuggingFace demo](#)**
-->
go to the root directory of your HSMR environment then copy run_obj_skin.py into exp subfolder then

```shell
# Single file wil be identified as a video by default if `--input_type` is not specified.
python exp/run_demo_oby.py --input_path "your/video/path/video.mp4"
```
On youtube you can watch the entire process.

How to run the code for processing a video:
[![Guarda il video](https://github.com/TheMich01/HSMR_to_mocap/blob/main/thumb/video01.png)](https://youtu.be/UTbyircAe5k?si=IgAqotZaaY3F6Ofr)

[This is the link to the complete playlist:](https://youtube.com/playlist?list=PLOBhaaonduFZAYvwuWpZIwUPSLNO7aX_t)
