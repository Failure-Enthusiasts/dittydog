
// this express server IS the gateway for localhost:4001, from external sources
// to the react app, which has the other half of this websocket. THIS is what
// we hit from our Docker app.

const express = require("express");
const http = require("http");
const socketIo = require("socket.io");
const cors = require('cors');

//Port from environment variable or default - 4001
const port = process.env.PORT || 4001;

//Setting up express and adding socketIo middleware
const app = express()
  .use(cors());

const server = http.createServer(app);
const io = socketIo(server, {
  allowEIO3: true,
  cors: {
    credentials: true,
    origin: "http://localhost:8080",
  }
});
//Setting up a socket with the namespace "connection" for new sockets
console.log("Middleware here.")
io.on("connection", socket => {
    console.log("New client connected");
    // socket.emit("incoming data", {'val1': 1, 'val2': 2}); # not needed
    console.log("This is the middleware's data:")

    //Here we listen on a new namespace called "incoming data"
    socket.on("incoming data", (data) => {
        //Here we broadcast it out to all other sockets EXCLUDING the socket which sent us the data
        // socket.broadcast.emit("incoming data", { num: data });
        console.log(data)
        socket.broadcast.emit("incoming data", data);
    });

    //A special namespace "disconnect" for when a client disconnects
    socket.on("disconnect", () => console.log("Client disconnected"));
});

server.listen(port, () => console.log(`Listening on port ${port}`));