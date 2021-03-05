window.myNameSpace = Object.assign({}, window.myNameSpace, {
    tabulator: {
        clipboardPasteAction: function(rowData, table) {
            console.log("Row data from paste parser");
            console.log(rowData);
        },
        clipboardPasted: function(clipboard, rowData, rows, table) {
            console.log("Paste registered");
            table.props.setProps({"clipboardPasted": rowData});
        }
    }
});
