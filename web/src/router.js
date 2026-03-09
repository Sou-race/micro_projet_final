import { createRouter, createWebHistory } from "vue-router"

import Connexion from "./views/connexion.vue"
import Inscription from "./views/inscription.vue"
import BenchmarkView from "./views/benchmark.vue"

const routes = [

  {
    path: "/",
    redirect: "/connexion"
  },

  {
    path: "/connexion",
    component: Connexion
  },

  {
    path: "/inscription",
    component: Inscription
  },

  {
    path: "/benchmark",
    component: BenchmarkView
  }

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
