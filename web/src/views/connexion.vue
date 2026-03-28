<template>
  <div class="auth-page">
    <div class="auth-box">
      <h2>Connexion</h2>
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Mot de passe" required />
      <button @click="handleLogin">Se connecter</button>
      <p v-if="message" class="msg-error">{{ message }}</p>
      <p>Pas de compte ? <router-link to="/inscription">Créer un compte</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const email = ref("")
const password = ref("")
const message = ref("")

const handleLogin = async () => {
  try {
    const response = await fetch("http://localhost:8000/prouteur/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email.value, password: password.value })
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
