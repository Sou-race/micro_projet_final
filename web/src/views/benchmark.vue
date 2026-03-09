<template>
  <div class="page">

    <h2 v-if="user">Bonjour {{ user.prenom }} 👋</h2>

    <button @click="logout">Logout</button>

    <hr>

    <h3>Lancer benchmark</h3>

    <select v-model="dataset">
      <option value="fashion_mnist">Fashion MNIST</option>
      <option value="cifar100">CIFAR100</option>
    </select>

    <button @click="startBenchmark">
      Lancer
    </button>

    <p>{{ message }}</p>

    <canvas id="benchmarkChart"></canvas>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import Chart from "chart.js/auto"

const router = useRouter()

const dataset = ref("fashion_mnist")
const message = ref("")
const user = ref(null)
const jobId = ref(null)

let chart = null
let interval = null

onMounted(() => {

  const storedUser = localStorage.getItem("user")

  if (!storedUser) {
    router.push("/connexion")
    return
  }

  user.value = JSON.parse(storedUser)

  const ctx = document.getElementById("benchmarkChart")

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "PyTorch accuracy",
          data: [],
          borderColor: "blue"
        },
        {
          label: "TensorFlow accuracy",
          data: [],
          borderColor: "red"
        }
      ]
    },
    options: {
      animation: false
    }
  })

})

const logout = () => {
  localStorage.removeItem("user")
  router.push("/connexion")
}

const startBenchmark = async () => {

  message.value = "Benchmark en cours..."

  const response = await fetch(
    "http://localhost:8000/prouteur/benchmark/start",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        dataset: dataset.value,
        epochs: 15
      })
    }
  )

  const data = await response.json()

  jobId.value = data.job_id

  interval = setInterval(updateStatus, 1500)
}

const updateStatus = async () => {

  if (!jobId.value) return

  const response = await fetch(
    `http://localhost:8000/prouteur/benchmark/status/${jobId.value}`
  )

  const data = await response.json()

  const pytorchHistory = data.results.pytorch.history
  const tfHistory = data.results.tensorflow.history

  chart.data.labels = pytorchHistory.map(p => p.epoch)

  chart.data.datasets[0].data = pytorchHistory.map(p => p.accuracy)
  chart.data.datasets[1].data = tfHistory.map(p => p.accuracy)

  chart.update()

  if (data.status === "finished") {

    message.value = "Benchmark terminé"

    clearInterval(interval)
  }

}
</script>

<style>
.page {
  padding: 40px;
}

canvas {
  margin-top: 40px;
  max-width: 700px;
}
</style>