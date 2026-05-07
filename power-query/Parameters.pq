// Parameters.pq
// ---------------------------------------------------------------------------
// Three small queries that pull configuration values out of the Settings
// sheet so users can change them without editing M code or VBA.
//
// Settings sheet layout (all on the "Settings" sheet, formatted as an
// Excel Table named "tblSettings" with two columns: Key, Value):
//
//   Key          | Value
//   -------------|--------------------------------
//   SheetName    | Data
//   DateColumn   | Date
//   LastFolder   | C:\path\to\source\folder
//
// Each query below returns a single text value. In Power Query, these
// queries should be referenced from the Parameters pFolder, pSheetName,
// and pDateColumn (Home > Manage Parameters > set "Current Value" to the
// query result, or just use the queries directly in SourceData and skip
// the formal Parameter objects).
// ---------------------------------------------------------------------------

// ===== fxSettings (helper) =====
let
    Source = Excel.CurrentWorkbook(){[Name = "tblSettings"]}[Content],
    Typed = Table.TransformColumnTypes(Source, {{"Key", type text}, {"Value", type text}})
in
    Typed

// ===== fxFolder =====
// let
//     Settings = fxSettings,
//     Match = Table.SelectRows(Settings, each [Key] = "LastFolder"),
//     Value = if Table.IsEmpty(Match) then error "LastFolder not set in Settings" else Match{0}[Value]
// in
//     Value

// ===== fxSheetName =====
// let
//     Settings = fxSettings,
//     Match = Table.SelectRows(Settings, each [Key] = "SheetName"),
//     Value = if Table.IsEmpty(Match) then error "SheetName not set in Settings" else Match{0}[Value]
// in
//     Value

// ===== fxDateColumn =====
// let
//     Settings = fxSettings,
//     Match = Table.SelectRows(Settings, each [Key] = "DateColumn"),
//     Value = if Table.IsEmpty(Match) then error "DateColumn not set in Settings" else Match{0}[Value]
// in
//     Value

// Note: each =====...===== block above is a SEPARATE query in Power Query.
// Create them one at a time via Get Data > Blank Query, paste the body
// (the `let ... in ...` portion), and name the query accordingly.
