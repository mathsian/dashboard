window.myNameSpace = Object.assign({}, window.myNameSpace, {
    tabulator: {
        clipboardPasteAction: function(rowData, table) {
            console.log("Row data from paste parser");
            console.log(rowData);
        },
        clipboardPasted: function(clipboard, rowData, rows, table) {
            console.log("Paste registered");
            table.props.setProps({"clipboardPasted": rowData});
        },
        groupHeader:
        function(value, count, data) {
            formatted = moment(value, "YYYY-MM-DD").format("dddd MMMM Do yyyy") + ", (" + count + ")";
            return formatted;
            },
        groupHeader2: [
            function(value, count, data) {
                formatted = moment(value, "YYYY-MM-DD").format("dddd MMMM Do yyyy") + ", (" + count + ")";
                return formatted;
            },
            function(value, count, data) {
                return value + ", (" + count + ")";
            }
        ],
        alertIcon: function(cell, formatterParams, onRendered) {
            data = cell.getData();
            value = "";
            if (data.present_today == 1) {
                value += "<i class='fas fa-exclamation'></i>";
            }
            if (data.authorised_today == 1) {
                value += "<i class='fas fa-question'></i>";
            }
            return value;
        },
        deleteRow: function(e, cell) {
            row = cell.getRow();
            if(this.confirm("Delete this concern about " + row.getData()["given_name"]+"?")){
                row.delete();
            }
        }
    }
});
