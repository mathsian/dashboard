window.myNameSpace = Object.assign({}, window.myNameSpace, {
    tabulator: {
        clipboardPasteAction: function(rowData, table) {
            console.warn("Row data from paste parser");
            console.warn(rowData);
        },
        clipboardPasted: function(clipboard, rowData, rows, table) {
            console.warn("Paste registered");
            table.props.setProps({"clipboardPasted": rowData});
        },
        groupHeader:
        function(value, count, data) {
            return moment(value, "YYYY-MM-DD").format("dddd MMMM Do yyyy") + ", (" + count + ")";
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
            let data = cell.getData();
            let value = "";
            if (data.present_today == 1) {
                value += "<i class='fas fa-exclamation'></i>";
            }
            if (data.authorised_today == 1) {
                value += "<i class='fas fa-question'></i>";
            }
            return value;
        },
        deleteRow: function(e, cell) {
            let row = cell.getRow();
            if(this.confirm("Delete this concern about " + row.getData()["given_name"]+"?")){
                row.delete();
            }
        },
        dataLoaded: function(data, table) {
                                console.warn("dataLoaded called");
                                console.warn(data);
                                var preselected = data.filter(row => row.selected == 1);
                            },
        tooltips: function(cell) {
            let cell_data = cell.getData();
            let field_name = cell.getField();
            let tt = "";
            if(field_name.includes('grade')) {
                tt = cell_data[field_name.replace('grade', 'comment')];
            } else {
                tt = cell.getValue();
            }
            return tt;
        },
        rowSelected: function(args) {
                                        console.warn("rowSelected called");
                                        console.warn("Args incoming");
                                        console.warn(args);
                                    }
    }
});
