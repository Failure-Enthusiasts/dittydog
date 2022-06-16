import { createApp } from 'vue'
import App from './App.vue'
import VueSocketIO from 'vue-3-socket.io'
// import SocketIO from 'socket.io-client'

const app = createApp(App)


app.use(new VueSocketIO({
  debug: true,
  connection: 'localhost:4001',
  vuex: {
      actionPrefix: 'SOCKET_',
      mutationPrefix: 'SOCKET_'
  }, //Optional options
}))

// export const SocketInstance = socketio('http://localhost:4001');
// createApp.use(VueSocketIO, SocketInstance)
app.mount('#app')
