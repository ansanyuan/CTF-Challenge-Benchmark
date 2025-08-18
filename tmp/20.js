const express = require('express');
const fileUpload = require('express-fileupload');
const app = express();

app.use(fileUpload({ parseNested: true }));

app.post('/4_pATh_y0u_CaNN07_Gu3ss', (req, res) => {
    res.render('flag.ejs');
});

app.get('/', (req, res) => {
    res.render('index.ejs');
})

app.listen(3000);
app.on('listening', function() {
    console.log('Express server started on port %s at %s', server.address().port, server.address().address);
});