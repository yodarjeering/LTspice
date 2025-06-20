Attribute VB_Name = "operateFile"
Option Explicit
#If VBA7 Then
    ' Office 2010以降 + 64ビット対応
    Private Declare PtrSafe Function SetCurrentDirectory Lib "kernel32" Alias "SetCurrentDirectoryA" (ByVal lpPathName As String) As Long
#Else
    ' 古いOffice（32ビット）用
    Private Declare Function SetCurrentDirectory Lib "kernel32" Alias "SetCurrentDirectoryA" (ByVal lpPathName As String) As Long
#End If



Public Function SelectFile(fileType As String) As Variant
    Dim selectFiles As Variant
    Dim fileFilter As String
    Dim extArray() As String

    SetCurrentDirectory ThisWorkbook.Path
    extArray = Split(fileType, ",")
    fileFilter = "対象ファイル (*." & Join(extArray, ";*.") & "),*." & Join(extArray, ";*.")
    
    selectFiles = Application.GetOpenFilename( _
        fileFilter:=fileFilter, _
        MultiSelect:=True, _
        Title:="ファイルを選択")

    If Not IsArray(selectFiles) Then
        MsgBox "ファイルが選択されていません。", vbExclamation
        Exit Function
    End If
    
    SelectFile = selectFiles
End Function


