<template>
  <div class="page-inscription">
    <form class="form-inscription" @submit.prevent="handleRegister">
      <h2>Inscription</h2>

      <input v-model="nom" type="text" placeholder="Nom" required />
      <input v-model="prenom" type="text" placeholder="Prénom" required />
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Mot de passe" required />
      <input
        v-model="confirmPassword"
        type="password"
        placeholder="Confirmer le mot de passe"
        required
      />

      <button type="submit">S'inscrire</button>

      <p v-if="message" class="message">{{ message }}</p>

      <div class="switch-section">
        <span>Déjà un compte ?</span>
        <button type="button" class="switch-button" @click="$emit('go-to-login')">
          Connectez vous
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue"

defineEmits(["go-to-login"])

const nom = ref("")
const prenom = ref("")
const email = ref("")
const password = ref("")
const confirmPassword = ref("")
const message = ref("")

const handleRegister = async () => {
  message.value = ""

  if (password.value !== confirmPassword.value) {
    message.value = "Les mots de passe ne correspondent pas"
    return
  }

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
      message.value = data.message
      nom.value = ""
      prenom.value = ""
      email.value = ""
      password.value = ""
      confirmPassword.value = ""
    } else {
      message.value = data.detail || "Erreur lors de l'inscription"
    }
  } catch (error) {
    message.value = "Serveur inaccessible"
  }
}
</script>

<style scoped>
.page-inscription {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f3f4f6;
}

.form-inscription {
  width: 360px;
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

h2 {
  text-align: center;
  margin-bottom: 8px;
}

input,
button {
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

.message {
  text-align: center;
  margin-top: 6px;
}

.switch-section {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}

.switch-button {
  background: transparent;
  color: #2563eb;
  border: 1px solid #2563eb;
}
</style>