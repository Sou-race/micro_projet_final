<template>
  <Connexion
    v-if="currentPage === 'connexion'"
    @go-to-register="currentPage = 'inscription'"
  />

  <Inscription
    v-else
    @go-to-login="currentPage = 'connexion'"
  />
</template>

<script setup>
import { ref } from "vue"
import Connexion from "./views/connexion.vue"
import Inscription from "./views/inscription.vue"

const currentPage = ref("connexion")
</script>