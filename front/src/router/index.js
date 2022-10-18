// import Vue from 'vue'
import {createRouter, createWebHistory} from 'vue-router'
import Main from '@/components/Main'
import Login from '@/components/Login'


// Vue.use(router)

const routes = [
    {
      path: '/',
      name: 'Main',
      component: Main
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;