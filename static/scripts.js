import fs from 'fs';




const url = '/getRegisters';

fetch(url, { method: 'GET', 'Allow-Control-Allow-Origin': '*' })
  .then(response => response.text())  
  .then(data => {
    console.log(data);
    console.log(fs)
  });