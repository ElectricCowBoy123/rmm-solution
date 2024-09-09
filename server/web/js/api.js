/* 
Chart.js
Node.js

*/

const express = require("express");
const axios = require("axios");
const os = require("os"); // Import the os module to get network interfaces
const app = express();
const port = 3000;

function getLocalIPAddress() {
  const interfaces = os.networkInterfaces();
  let localIP = "";
  for (let iface in interfaces) {
    for (let details of interfaces[iface]) {
      // Check if the address is IPv4 and not internal (i.e., not localhost)
      if (details.family === "IPv4" && !details.internal) {
        localIP = details.address;
        console.log(localIP);
        break;
      }
    }
    if (localIP) break;
  }

  return localIP;
}

app.use(express.json());
// Example route
app.get("/api/data", async (req, res) => {
  try {
    const localIP = getLocalIPAddress();
    const response = await axios.get(`http://172.16.0.20:5000/performance`);
    const jsonObj = response.data; // No need to parse as it is already an object
    console.log(jsonObj.cpu.cpu_freq.current);
    res.json(jsonObj);
  } catch (error) {
    console.error("Error:", error.message); // Log the error for better debugging
    res.status(500).send("Error fetching data from Python API");
  }
});

// Function to get the server IP addresses
function getIPAddress() {
  const interfaces = os.networkInterfaces();
  let addresses = [];

  for (let iface in interfaces) {
    for (let ifaceInfo of interfaces[iface]) {
      // Skip over non-IPv4 and internal (i.e., localhost) addresses
      if (ifaceInfo.family === "IPv4" && !ifaceInfo.internal) {
        addresses.push(ifaceInfo.address);
      }
    }
  }

  return addresses.length > 0 ? addresses : ["127.0.0.1"];
}

app.listen(port, () => {
  const ipAddresses = getIPAddress();
  ipAddresses.forEach((ip) => {
    console.log(`Node.js API server running on http://${ip}:${port}/api/data`);
  });
});
