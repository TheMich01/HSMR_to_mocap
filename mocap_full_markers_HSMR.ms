-- Script per animare dummy points sui vertici specificati in 3ds Max 2018
fn animateDummySequence startFilePath = (
    print "Inizio funzione animateDummySequence"
    print ("Start file: " + startFilePath)
    
    -- Estrai il percorso base e il prefisso
    local basePath = getFilenamePath startFilePath
    local prefix = "skin_frame_"
    print ("Base path: " + basePath)
    print ("Prefix: " + prefix)
    
    -- Conta i frame
    local frameCount = 0
    local i = 0
    local testFile = basePath + prefix + (formattedPrint i format:"03d") + ".obj"
    while doesFileExist testFile do (
        frameCount += 1
        i += 1
        testFile = basePath + prefix + (formattedPrint i format:"03d") + ".obj"
    )
    if frameCount == 0 do (
        messageBox "Errore: nessun file trovato!"
        return undefined
    )
    print ("Trovati " + (frameCount as string) + " frame")
    
    -- Imposta la timeline
    animationRange = interval 0 (frameCount - 1)
    
    -- Carica la mesh base (frame 0)
    local baseObjName = uniqueName "BaseMesh"
    importFile startFilePath #noPrompt using:ObjImp
    local baseObj = selection[1]
    if baseObj == undefined do (
        messageBox "Errore: non riesco a caricare il primo file OBJ!"
        return undefined
    )
    baseObj.name = baseObjName
    update baseObj
    local vertCount = getNumVerts baseObj
    print ("Base object caricato: " + baseObj.name)
    print ("Numero vertici base: " + (vertCount as string))
    
    -- Lista dei vertici da tracciare
    local targetVerts = #(5525, 5595, 5663, 5061, 5126, 4915, 5310, 4390, 4465, 4530, 4568, 4621, 6728, 6777, 6748, 6680, 5263, 6537, 5295, 6318, 3645, 3694, 2193, 2135, 2185, 1599, 1736, 1444, 1238, 849, 980, 1043, 1068, 1113, 3328, 3378, 3369, 3315, 1801, 3114, 1834, 2857, 135, 182)
    local dummies = #()
    
    -- Crea i dummy per i vertici specificati
    for v in targetVerts do (
        local vertPos = getVert baseObj v
        local dummyObj = point name:("Dummy_" + v as string) pos:vertPos size:0.1
        append dummies dummyObj
        print ("Creato " + dummyObj.name + " alla posizione " + (vertPos as string))
    )
    
    -- Anima i dummy frame per frame
    set animate on
    for i = 1 to frameCount - 1 do ( -- Partiamo da 1, frame 0 è la base
        local frameFile = basePath + prefix + (formattedPrint i format:"03d") + ".obj"
        print ("Processing frame: " + frameFile + " at time " + (i as string))
        if doesFileExist frameFile then (
            deselect $*
            importFile frameFile #noPrompt using:ObjImp
            local tempObj = selection[1]
            if tempObj != undefined then (
                tempObj.name = uniqueName "TempMesh"
                update tempObj
                print ("Temp mesh caricata: " + tempObj.name)
                sliderTime = i
                toolMode.coordsys #world
                
                -- Anima ogni dummy
                for d = 1 to targetVerts.count do (
                    local vertIdx = targetVerts[d]
                    local vertPos = getVert tempObj vertIdx
                    dummies[d].pos = vertPos
                    print (dummies[d].name + " spostato a " + (vertPos as string) + " al frame " + (i as string))
                )
                
                delete tempObj
                print ("Temp mesh eliminata")
            ) else (
                print ("Errore: non trovo " + frameFile)
            )
        ) else (
            print ("File mancante: " + frameFile)
        )
    )
    set animate off
    sliderTime = 0
    print "Fine animazione"
    
    print "Animazione completata nella funzione"
    baseObj
)

-- Esegui lo script
print "Apertura finestra di selezione file"
firstFile = getOpenFileName caption:"Seleziona il primo file OBJ della sequenza" types:"OBJ (*.obj)|*.obj"
if firstFile != undefined then (
    print ("File selezionato: " + firstFile)
    result = animateDummySequence firstFile
    if result != undefined then (
        redrawViews()
        print "Animazione completata!"
    ) else (
        print "Errore durante l'animazione"
    )
) else (
    print "Nessun file selezionato"
)
