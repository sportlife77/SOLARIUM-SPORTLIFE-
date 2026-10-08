Set shell = CreateObject("WScript.Shell")
Set fs = CreateObject("Scripting.FileSystemObject")
folder = fs.GetParentFolderName(WScript.ScriptFullName)
target = fs.BuildPath(folder, "Reservas-Solarium.html")
Set shortcut = shell.CreateShortcut(shell.SpecialFolders("Desktop") & "\Sport Life - Reservas Solarium.lnk")
shortcut.TargetPath = target
shortcut.WorkingDirectory = folder
shortcut.Description = "Sport Life - Reservas Solarium"
shortcut.Save
MsgBox "Acceso creado en el escritorio. Abrilo con doble clic.", 64, "Sport Life"
