var table = $('#dataTable').DataTable({
  "ajax": {
      "url": "http://127.0.0.1:8000/api/employee-data", // Fetch data from the FastAPI backend
      "dataSrc": "data", // The 'data' key in the JSON response will be used for the table
  },
  "columns": [
      { "data": "name" },
      { "data": "position" },
      { "data": "office" },
      { "data": "age" },
      { "data": "date_of_joining" },
      { "data": "salary" }
  ],
  "pageLength": 5,
        "lengthMenu": [5, 10, 25, 50], // Options for number of entries per page
        "processing": true, // Show loading indicator while fetching data
        "serverSide": false, // Data is already processed by the API
        "paging": true, // Enable pagination
        "responsive": true, // Make the table responsive on smaller screens
        "autoWidth": true// Enable pagination
});

// Refresh the DataTable every 5 seconds by reloading the data
function reloadTable(){
  table.ajax.reload();
}