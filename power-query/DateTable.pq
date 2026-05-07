// DateTable
// ---------------------------------------------------------------------------
// Generates a contiguous calendar covering the date range present in
// SourceData, padded out to full years on each end so YoY/YTD calcs work
// cleanly. Loads to the Data Model.
//
// In Power Pivot:
//   1. Mark this table as a Date Table (Date Table > Mark as Date Table,
//      pick the Date column).
//   2. Create a relationship: SourceData[<DateColumn>] -> DateTable[Date].
// ---------------------------------------------------------------------------
let
    SourceDates = Table.SelectColumns(SourceData, {pDateColumn}),
    Renamed = Table.RenameColumns(SourceDates, {{pDateColumn, "Date"}}),
    NonNull = Table.SelectRows(Renamed, each [Date] <> null),

    MinDate = List.Min(NonNull[Date]),
    MaxDate = List.Max(NonNull[Date]),

    StartDate = #date(Date.Year(MinDate), 1, 1),
    EndDate = #date(Date.Year(MaxDate), 12, 31),
    DayCount = Duration.Days(EndDate - StartDate) + 1,

    DateList = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    AsTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    TypedDate = Table.TransformColumnTypes(AsTable, {{"Date", type date}}),

    AddYear = Table.AddColumn(TypedDate, "Year", each Date.Year([Date]), Int64.Type),
    AddQuarterNum = Table.AddColumn(AddYear, "QuarterNum", each Date.QuarterOfYear([Date]), Int64.Type),
    AddQuarter = Table.AddColumn(AddQuarterNum, "Quarter", each "Q" & Text.From([QuarterNum]), type text),
    AddMonthNum = Table.AddColumn(AddQuarter, "MonthNum", each Date.Month([Date]), Int64.Type),
    AddMonthName = Table.AddColumn(AddMonthNum, "MonthName", each Date.MonthName([Date]), type text),
    AddYearMonth = Table.AddColumn(AddMonthName, "YearMonth", each Date.ToText([Date], "yyyy-MM"), type text),
    AddDay = Table.AddColumn(AddYearMonth, "Day", each Date.Day([Date]), Int64.Type),
    AddDayOfWeekNum = Table.AddColumn(AddDay, "DayOfWeekNum", each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),
    AddDayName = Table.AddColumn(AddDayOfWeekNum, "DayName", each Date.DayOfWeekName([Date]), type text)
in
    AddDayName
