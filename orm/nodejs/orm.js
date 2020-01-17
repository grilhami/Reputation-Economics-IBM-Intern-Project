var ibmdb = require('ibm_db'), 
    koneksi = "DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-dal09-03.services.dal.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=ffz03558;PWD=6s50g+3tr7slj5cb;";

ibmdb.open(koneksi, function(err, conn) {
  if(err) {
    return console.log(err);
  }

  conn.query('select * from FFZ03558.SOURCE fetch first 5 rows only', function(err, data) {
    if(err) {
      console.log(err);
    }
    else {
      console.log(data);
    }

    conn.close(function() {
      console.log('done');
    });

  });
});