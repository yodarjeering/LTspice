Attribute VB_Name = "Main"
Sub Main()
    
'------------------------- ccf/net/lst�t�@�C���̑I�����W�b�N----------------------
    Dim ws As Worksheet
    Dim selectFiles As Variant                        ' �I�������t�@�C���̃p�X���i�[
    Dim fso As Object
    Dim fileExt As String
    Dim ccfCount As Integer, netCount As Integer, lstCount As Integer
    Dim i As Long
    

    ' ���샂�W���[��
    selectFiles = operateFile.SelectFile("ccf,net,lst")
    If IsEmpty(selectFiles) Then Exit Sub
    
    ' �g���q�̃`�F�b�N
    Set fso = CreateObject("Scripting.FileSystemObject")
    For i = LBound(selectFiles) To UBound(selectFiles)
        fileExt = LCase(fso.GetExtensionName(selectFiles(i)))
        Select Case fileExt
            Case "ccf": ccfCount = ccfCount + 1
            Case "net": netCount = netCount + 1
            Case "lst": lstCount = lstCount + 1
            Case Else
                MsgBox "�����ȃt�@�C���`�����܂܂�Ă��܂�: " & selectFiles(i), vbCritical
                Exit Sub
        End Select
    Next i

    ' �I���p�^�[���̌���
    If Not (ccfCount > 0 And netCount = 0 And lstCount = 0) _
    And Not (ccfCount = 0 And netCount = 1 And lstCount = 1) Then
        MsgBox "�t�@�C���̑g�ݍ��킹�������ł��B" & vbCrLf & _
            "�ECCF�t�@�C���̂�" & vbCrLf & "�E�܂��� NET+PKG ��2�t�@�C����I�����Ă��������B", vbCritical
        Exit Sub
    End If

    ' ����Ƀt�@�C���I�����ꂽ�ꍇ
    Set ws = ThisWorkbook.Worksheets("main")
    'MsgBox "�t�@�C���I�������F" & vbCrLf & Join(SelectFiles, vbCrLf)

    
'-------------------------------- �V�[�g�upyCode�v�Ƀt�@�C���̃p�X�������o�����W�b�N----------------
    ' ������ SelectFiles() ���g���ď����𑱂���
    ' ��: ws.Cells(1, 1).Value = SelectFiles(1)
        ' �p�X���X���b�V���`���ŃZ���ɏo�́i��: A1 ����j
    Dim pyCodeSheet As Worksheet
    Set pyCodeSheet = ThisWorkbook.Worksheets("pyCode")

    Dim CFG_FILE_PATH As String
    Dim LST_FILE_PATH As String
    Dim NET_FILE_PATH As String
    Dim OUTPUT_DIR As String
    Dim filePath As String
    Dim ext As String
    Dim currentDir As String
    Dim searchKeyword As String
    Dim resultCell As Range
    Dim assignValue As String
    
    
    ' OUTPUT_DIR �̏������݁i�L�[���[�h�����ɕύX�j
    currentDir = CurDir & "/output"
    searchKeyword = "OUTPUT_DIR"
    assignValue = searchKeyword & " = " & Chr(34) & Replace(currentDir, "\", "/") & Chr(34)
    Set resultCell = pyCodeSheet.Cells.Find(What:=searchKeyword, LookIn:=xlValues, LookAt:=xlPart)
    If Not resultCell Is Nothing Then
        resultCell.Value = assignValue
    Else
        MsgBox "[" & searchKeyword & "] �� pyCode �V�[�g���Ō�����܂���ł����B", vbExclamation
    End If

    ' �e�t�@�C���ɑ΂��Ċg���q�𔻒肵�ē��I�ɏ�������
    For i = LBound(selectFiles) To UBound(selectFiles)
        filePath = selectFiles(i)
        ext = LCase(fso.GetExtensionName(filePath))

        Select Case ext
            Case "ccf"
                searchKeyword = "CCF_FILE_PATH"
                assignValue = searchKeyword & " = " & Chr(34) & Replace(filePath, "\", "/") & Chr(34)
            Case "lst"
                searchKeyword = "LST_FILE_PATH"
                assignValue = searchKeyword & " = " & Chr(34) & Replace(filePath, "\", "/") & Chr(34)
            Case "net"
                searchKeyword = "NET_FILE_PATH"
                assignValue = searchKeyword & " = " & Chr(34) & Replace(filePath, "\", "/") & Chr(34)
            Case Else
                MsgBox "���Ή��̊g���q: " & ext, vbExclamation
                GoTo ContinueNext
        End Select

        ' �V�[�g������Y���L�[���[�h���������ď㏑��
        Set resultCell = pyCodeSheet.Cells.Find(What:=searchKeyword, LookIn:=xlValues, LookAt:=xlPart)
        If Not resultCell Is Nothing Then
            resultCell.Value = assignValue
        Else
            MsgBox "[" & searchKeyword & "] �� pyCode �V�[�g���Ō�����܂���ł����B", vbExclamation
        End If
ContinueNext:
    Next i
    Call operatePython.WritePythonFile

End Sub

Sub test()
    Call operatePython.WritePythonFile
End Sub





