<template>
  <div class="auth-page">
    <div class="auth-box">
      <h2>Inscription</h2>
      <input v-model="nom" placeholder="Nom" required />
      <input v-model="prenom" placeholder="Prénom" required />
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Mot de passe" required />
      <button @click="handleRegister">Créer le compte</button>
      <p v-if="message" class="msg-error">{{ message }}</p>
      <p>Déjà inscrit ? <router-link to="/connexion">Se connecter</router-link></p>
    </div>
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
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nom: nom.value, prenom: prenom.value, email: email.value, password: password.value })
    })
    const data = await response.json()
    if (response.ok) {
      localStorage.setItem("user", JSON.stringify(data.user))
      router.push("/benchmark")
    } else {
      message.value = data.detail
    }
  } catch {
    message.value = "Serveur inaccessible"
  }
}
</script>
