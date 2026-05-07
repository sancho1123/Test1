Attribute VB_Name = "modDashboard"
Option Explicit

' ---------------------------------------------------------------------------
' modDashboard
'
' Refresh entry point for the dashboard. Prompts the user for the source
' folder, writes the path to the Settings sheet, and triggers a full refresh
' of the Power Query / Power Pivot data model.
'
' Wire RefreshDashboard to a button on the Dashboard sheet.
' ---------------------------------------------------------------------------

Private Const SETTINGS_SHEET   As String = "Settings"
Private Const NAMED_FOLDER     As String = "LastFolder"
Private Const NAMED_SHEETNAME  As String = "SheetName"
Private Const NAMED_DATECOLUMN As String = "DateColumn"

Public Sub RefreshDashboard()
    Dim folderPath As String
    folderPath = PickFolder()
    If LenB(folderPath) = 0 Then Exit Sub

    If Not ValidateSettings() Then Exit Sub

    SetNamedValue NAMED_FOLDER, folderPath

    Application.ScreenUpdating = False
    Application.Cursor = xlWait
    Application.StatusBar = "Refreshing dashboard from " & folderPath & "..."

    On Error GoTo Fail
    ThisWorkbook.RefreshAll
    DoEvents
    ThisWorkbook.Model.Refresh
    On Error GoTo 0

    Application.StatusBar = False
    Application.Cursor = xlDefault
    Application.ScreenUpdating = True
    MsgBox "Dashboard refreshed from:" & vbCrLf & folderPath, vbInformation, "Refresh complete"
    Exit Sub

Fail:
    Application.StatusBar = False
    Application.Cursor = xlDefault
    Application.ScreenUpdating = True
    MsgBox "Refresh failed:" & vbCrLf & vbCrLf & Err.Description, vbExclamation, "Refresh error"
End Sub

Private Function PickFolder() As String
    Dim fd As FileDialog
    Dim defaultPath As String
    defaultPath = GetNamedValue(NAMED_FOLDER)

    Set fd = Application.FileDialog(msoFileDialogFolderPicker)
    With fd
        .Title = "Select the folder containing the source .xlsx files"
        .AllowMultiSelect = False
        If LenB(defaultPath) > 0 Then .InitialFileName = defaultPath
        If .Show = -1 Then PickFolder = .SelectedItems(1)
    End With
End Function

Private Function ValidateSettings() As Boolean
    Dim sheetName As String, dateCol As String
    sheetName = GetNamedValue(NAMED_SHEETNAME)
    dateCol = GetNamedValue(NAMED_DATECOLUMN)

    If LenB(sheetName) = 0 Or LenB(dateCol) = 0 Then
        MsgBox "Open the '" & SETTINGS_SHEET & "' sheet and fill in SheetName and DateColumn before refreshing.", _
               vbExclamation, "Settings missing"
        ValidateSettings = False
        Exit Function
    End If
    ValidateSettings = True
End Function

Private Function GetNamedValue(ByVal namedRange As String) As String
    On Error Resume Next
    GetNamedValue = CStr(ThisWorkbook.Names(namedRange).RefersToRange.Value)
    On Error GoTo 0
End Function

Private Sub SetNamedValue(ByVal namedRange As String, ByVal value As String)
    ThisWorkbook.Names(namedRange).RefersToRange.Value = value
End Sub
