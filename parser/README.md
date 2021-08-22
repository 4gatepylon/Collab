# Excel Document Structure
Prototypical Excel Structure for Hello World File:
```
├── [Content_Types].xml
├── _rels
├── docProps
│   ├── app.xml
│   └── core.xml
└── xl
    ├── _rels
    │   └── workbook.xml.rels
    ├── sharedStrings.xml
    ├── styles.xml
    ├── theme
    │   └── theme1.xml
    ├── workbook.xml
    └── worksheets
        └── sheet1.xml
```

We can probably ignore `theme/` and `styles.xml`.

`[Content_Types].xml` encodes the filestructure (i.e. where the files inside the tree is). It also encodes the type of information that is stored in each (i.e. the content type, duh). **This is the master document for the XSLX**.

According this this master document `app.xml` encodes "extended properties" and `core.xml` (in `docProps`) encodes "core properties". For me the extended properties are primarily information about where the document was generated (i.e. I created it in Microsoft Excel Online with App Version 16.0300). It contains other metadata like the manager and company. For me the core properties include things like the "subject", creator, and a dc:description + cp:keywords (unclear exactly what these are) and other such propetrties. These can probably be ignored.

`_rels` seems to have primarily metadata for where the get information about the types of relationships. I think this is irrelevant for our MVP.

Inside sheet files in `worksheets` you will find information about what to open the Excel file to when you open it. For example, you might want to open to the first tab with active cell C9 (etc...). We care primarily about `<sheetData>` I think. You will find a sructure like this:
```
<row r="1" spans="1:7">
    <c r="A1" t="s">
        <v>0</v>
    </c>
    <c r="C1" t="s">
        <v>1</v>
    </c>
    <c r="D1" t="s">
        <v>1</v>
    </c>
    <c r="G1">
        <f>SUM(C2:C9)</f>
        <v>36</v>
    </c>
</row>
```



It is unclear why there is a 0 at "A1" since there I have "hello world".

`workbook.xml` looks like this for a hello world I made:
```
<workbook _redacted_not_important_ >
    <fileVersion _redacted_not_important_/>
    <workbookPr _redacted_not_important_/>
    <xr:revisionPtr _redacted_not_important_ _file_rebuilt_means_irrelevant_/>
    <bookViews>
        _seems_to_be_gui_stuff_
    </bookViews>
    <sheets>
        _important_this_is_the_tab_at_the_bottom_
        <sheet name="Sheet1" sheetId="1" r:id="rId1"/>
    </sheets>
    <calcPr calcId="191028"/>
    <extLst>
        <ext uri="{B58B0392-4F1F-4190-BB64-5DF3571DCE5F}"
            xmlns:xcalcf="http://schemas.microsoft.com/office/spreadsheetml/2018/calcfeatures">
            <xcalcf:calcFeatures>
                <xcalcf:feature name="microsoft.com:RD"/>
                <xcalcf:feature name="microsoft.com:Single"/>
                <xcalcf:feature name="microsoft.com:FV"/>
                <xcalcf:feature name="microsoft.com:CNMTM"/>
                <xcalcf:feature name="microsoft.com:LET_WF"/>
            </xcalcf:calcFeatures>
        </ext>
    </extLst>
</workbook>
```