Attribute VB_Name = "operateFile"
Option Explicit
#If VBA7 Then
    ' Office 2010�ȍ~ + 64�r�b�g�Ή�
    Private Declare PtrSafe Function SetCurrentDirectory Lib "kernel32" Alias "SetCurrentDirectoryA" (ByVal lpPathName As String) As Long
#Else
    ' �Â�Office�i32�r�b�g�j�p
    Private Declare Function SetCurrentDirectory Lib "kernel32" Alias "SetCurrentDirectoryA" (ByVal lpPathName As String) As Long
#End If



Public Function SelectFile(fileType As String) As Variant
    Dim selectFiles As Variant
    Dim fileFilter As String
    Dim extArray() As String

    SetCurrentDirectory ThisWorkbook.Path
    extArray = Split(fileType, ",")
    fileFilter = "�Ώۃt�@�C�� (*." & Join(extArray, ";*.") & "),*." & Join(extArray, ";*.")
    
    selectFiles = Application.GetOpenFilename( _
        fileFilter:=fileFilter, _
        MultiSelect:=True, _
        Title:="�t�@�C����I��")

    If Not IsArray(selectFiles) Then
        MsgBox "�t�@�C�����I������Ă��܂���B", vbExclamation
        Exit Function
    End If
    
    SelectFile = selectFiles
End Function


