<template>
  <div class="page-connexion">
    <form class="form-connexion" @submit.prevent="handleLogin">
      <h2>Connexion</h2>
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Mot de passe" required />
      <button type="submit">Se connecter</button>
      <p v-if="message">{{ message }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue"

const email = ref("")
const password = ref("")
const message = ref("")

const handleLogin = async () => {
  try {
    const response = await fetch("http://localhost:8000/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    })

    const data = await response.json()

    if (response.ok) {
      message.value = data.message
      localStorage.setItem("user", JSON.stringify(data.user))
    } else {
      message.value = data.detail || "Erreur de connexion"
    }
  } catch (error) {
    message.value = "Serveur inaccessible"
  }
}
</script>

<style scoped>
.page-connexion {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f3f4f6;
}

.form-connexion {
  width: 320px;
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

input, button {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

button {
  background: #2563eb;
  color: white;
  border: none;
  cursor: pointer;
}
</style>