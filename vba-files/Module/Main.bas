Attribute VB_Name = "Main"
Sub Main()
    
'------------------------- ccf/net/lstファイルの選択ロジック----------------------
    Dim ws As Worksheet
    Dim selectFiles As Variant                        ' 選択したファイルのパスを格納
    Dim fso As Object
    Dim fileExt As String
    Dim ccfCount As Integer, netCount As Integer, lstCount As Integer
    Dim i As Long
    

    ' 自作モジュール
    selectFiles = operateFile.SelectFile("ccf,net,lst")
    If IsEmpty(selectFiles) Then Exit Sub
    
    ' 拡張子のチェック
    Set fso = CreateObject("Scripting.FileSystemObject")
    For i = LBound(selectFiles) To UBound(selectFiles)
        fileExt = LCase(fso.GetExtensionName(selectFiles(i)))
        Select Case fileExt
            Case "ccf": ccfCount = ccfCount + 1
            Case "net": netCount = netCount + 1
            Case "lst": lstCount = lstCount + 1
            Case Else
                MsgBox "無効なファイル形式が含まれています: " & selectFiles(i), vbCritical
                Exit Sub
        End Select
    Next i

    ' 選択パターンの検証
    If Not (ccfCount > 0 And netCount = 0 And lstCount = 0) _
    And Not (ccfCount = 0 And netCount = 1 And lstCount = 1) Then
        MsgBox "ファイルの組み合わせが無効です。" & vbCrLf & _
            "・CCFファイルのみ" & vbCrLf & "・または NET+PKG の2ファイルを選択してください。", vbCritical
        Exit Sub
    End If

    ' 正常にファイル選択された場合
    Set ws = ThisWorkbook.Worksheets("main")
    'MsgBox "ファイル選択完了：" & vbCrLf & Join(SelectFiles, vbCrLf)

    
'-------------------------------- シート「pyCode」にファイルのパスを書き出すロジック----------------
    ' ここで SelectFiles() を使って処理を続ける
    ' 例: ws.Cells(1, 1).Value = SelectFiles(1)
        ' パスをスラッシュ形式でセルに出力（例: A1 から）
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
    
    
    ' OUTPUT_DIR の書き込み（キーワード検索に変更）
    currentDir = CurDir & "/output"
    searchKeyword = "OUTPUT_DIR"
    assignValue = searchKeyword & " = " & Chr(34) & Replace(currentDir, "\", "/") & Chr(34)
    Set resultCell = pyCodeSheet.Cells.Find(What:=searchKeyword, LookIn:=xlValues, LookAt:=xlPart)
    If Not resultCell Is Nothing Then
        resultCell.Value = assignValue
    Else
        MsgBox "[" & searchKeyword & "] が pyCode シート内で見つかりませんでした。", vbExclamation
    End If

    ' 各ファイルに対して拡張子を判定して動的に書き込む
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
                MsgBox "未対応の拡張子: " & ext, vbExclamation
                GoTo ContinueNext
        End Select

        ' シート内から該当キーワードを検索して上書き
        Set resultCell = pyCodeSheet.Cells.Find(What:=searchKeyword, LookIn:=xlValues, LookAt:=xlPart)
        If Not resultCell Is Nothing Then
            resultCell.Value = assignValue
        Else
            MsgBox "[" & searchKeyword & "] が pyCode シート内で見つかりませんでした。", vbExclamation
        End If
ContinueNext:
    Next i
    Call operatePython.WritePythonFile

End Sub

Sub test()
    Call operatePython.WritePythonFile
End Sub





