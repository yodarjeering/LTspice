Attribute VB_Name = "operatePython"


Sub WritePythonFile()
    Dim pyFile As String
    Dim pyCode As String
    Dim fso As Object
    Dim f As Object
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim lineText As String
    Dim pythonExe As String
    Dim shellCommand As String

    If ThisWorkbook.Path = "" Then
        MsgBox "このExcelファイルを保存してから実行してください。", vbExclamation
        Exit Sub
    End If

    pyFile = ThisWorkbook.Path & "\temp_script.py"
    Set ws = ThisWorkbook.Sheets("pyCode")
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row

    ' UTF-8 エンコーディング宣言を追加
    'pyCode = "# -*- coding: utf-8 -*-" & vbCrLf

    For i = 1 To lastRow
        If Not IsEmpty(ws.Cells(i, 1).Value) Then
            lineText = ws.Cells(i, 1).Value

            ' 不可視スペース類をすべて半角スペースに統一
            lineText = Replace(lineText, ChrW(160), " ")   ' ノーブレークスペース
            lineText = Replace(lineText, ChrW(12288), " ") ' 全角スペース
            lineText = Replace(lineText, vbTab, "    ")    ' タブ → スペース4つ
            pyCode = pyCode & lineText & vbCrLf
        End If
    Next i

    Set fso = CreateObject("Scripting.FileSystemObject")
    Set f = fso.CreateTextFile(pyFile, True)
    f.Write pyCode
    f.Close

    ' 書き込み直後のラグ対策
    Application.Wait Now + TimeValue("00:00:01")

    ' Pythonファイルをコマンドプロンプト経由で実行し、明示的にターミナル表示を促す
    pythonExe = "py" ' または "C:\Path\to\python.exe"
    shellCommand = "cmd.exe /k title Python Terminal && " & pythonExe & " " & Chr(34) & pyFile & Chr(34) ' <= cmd.exe / kだと実行後ターミナルが閉じない
    'shellCommand = "cmd.exe /c title Python Terminal && " & pythonExe & " " & Chr(34) & pyFile & Chr(34)
    Shell shellCommand, vbNormalFocus

End Sub

