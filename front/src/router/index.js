// import Vue from 'vue'
import {createRouter, createWebHistory} from 'vue-router'
import Main from '@/components/Main'
import Login from '@/components/Login'


// Vue.use(router)

const routes = [
    {
      path: '/',
      name: 'Login',
      component: Login
    },
    {
      path: '/playlist',
      name: 'Main',
      component: Main
    }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;