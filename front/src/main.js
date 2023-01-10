import { createApp} from 'vue'
import App from './App.vue'
import VueSocketIO from 'vue-3-socket.io'
import router from './router'
// import router from './router'
// import SocketIO from 'socket.io-client'

const app = createApp(App)
app.config.globalProperties.$hostname = 'http://localhost:8080'

app.use(
  new VueSocketIO({
    debug: true,
    connection: 'localhost:4001',
    vuex: {
        actionPrefix: 'SOCKET_',
        mutationPrefix: 'SOCKET_'
    }, //Optional options
  })
)
app.use(router)

// export const SocketInstance = socketio('http://localhost:4001');
// createApp.use(VueSocketIO, SocketInstance)
// app.use(router);
app.mount('#app')
