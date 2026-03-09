<template>

<div class="page">

<form @submit.prevent="handleRegister">

<h2>Inscription</h2>

<input v-model="nom" placeholder="Nom" required>

<input v-model="prenom" placeholder="Prénom" required>

<input v-model="email" type="email" placeholder="Email" required>

<input v-model="password" type="password" placeholder="Mot de passe" required>

<button type="submit">Créer le compte</button>

<p v-if="message">{{ message }}</p>

<p>
Déjà inscrit ?
<router-link to="/connexion">Se connecter</router-link>
</p>

</form>

</div>

</template>

<script setup>

import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

const nom = ref("")
const prenom = ref("")
const email = ref("")
const password = ref("")
const message = ref("")

const handleRegister = async () => {

  try {

    const response = await fetch("http://localhost:8000/prouteur/api/register", {

      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        nom: nom.value,
        prenom: prenom.value,
        email: email.value,
        password: password.value
      })

    })

    const data = await response.json()

    if (response.ok) {

      localStorage.setItem("user", JSON.stringify(data.user))

      router.push("/benchmark")

    } else {

      message.value = data.detail

    }

  } catch (error) {

    message.value = "Serveur inaccessible"

  }

}

</script>

<style scoped>

.page {
display:flex;
justify-content:center;
align-items:center;
height:100vh;
}

form {
background:white;
padding:30px;
border-radius:10px;
display:flex;
flex-direction:column;
gap:10px;
width:300px;
}

input,button {
padding:10px;
border-radius:6px;
border:1px solid #ccc;
}

button {
background:#2563eb;
color:white;
border:none;
}

</style>