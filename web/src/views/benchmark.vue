<template>
  <div style="display:flex; flex-direction:column; min-height:100vh;">

    <header class="topbar">
      <h2>Deep learning benchmark <span v-if="isAdmin" class="badge">Admin</span></h2>
      <div class="topbar-actions">
        <span v-if="user">{{ user.prenom }} {{ user.nom }}</span>
        <button class="btn-danger" @click="logout">Déconnexion</button>
      </div>
    </header>

    <div class="controls">
      <select v-model="dataset">
        <option value="fashion_mnist">Fashion MNIST</option>
        <option value="cifar100">CIFAR-100</option>
      </select>
      <button @click="startBenchmark" :disabled="running">
        {{ running ? "En cours..." : "Lancer" }}
      </button>
      <span v-if="message" class="status-msg">{{ message }}</span>
    </div>

    <div class="charts-grid">
      <div class="chart-card">
        <h4>Accuracy par epoch</h4>
        <canvas id="chartAccuracy"></canvas>
      </div>
      <div class="chart-card">
        <h4>Temps d'exécution cumulé (s)</h4>
        <canvas id="chartSpeed"></canvas>
      </div>
      <div class="chart-card" v-if="isAdmin">
        <h4>CPU moyen par epoch (%)</h4>
        <canvas id="chartCpu"></canvas>
      </div>
      <div class="chart-card" v-if="isAdmin">
        <h4>RAM moyenne par epoch (Go)</h4>
        <canvas id="chartRam"></canvas>
      </div>
    </div>

    <footer>
      <div>
        <h5>CGU</h5>
        <p>
          Cette application a été developpée dans le cadre de la matière microservices.<br>
          Les données utilisateurs sont stockées dans une bdd sécurisée.<br>
          L'utilisation est réservée aux membres du groupe de projet et au professeur Raphael chargé de l'évaluation.
        </p>
      </div>
      <div>
        <h5>Contacts</h5>
        <address>
          Khadija Bourrich-ING3 IA<br>
          <a href="mailto:bourrichkh@cy-tech.fr">bourrichkh@cy-tech.fr</a><br>
        </address>
        <address>
          Pierre Antoine Cassard-ING3 IA<br>
          <a href="mailto:cassardpie@cy-tech.fr">cassardpie@cy-tech.fr</a><br>
        </address>
        <address>
          Simon Carriac-ING3 IA<br>
          <a href="mailto:carriacsim@cy-tech.fr">carriacsim@cy-tech.fr</a><br>
        </address>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue"
import { useRouter } from "vue-router"
import Chart from "chart.js/auto"

const router = useRouter()
const dataset = ref("fashion_mnist")
const message = ref("")
const user = ref(null)
const jobId = ref(null)
const running = ref(false)

const isAdmin = computed(() => {
  if (!user.value) return false
  const v = user.value.admin
  return v === true || v === "True" || v === "true" || v === 1
})

let charts = {}
let interval = null

const COLORS = {
  blue: "#1a1aff",
  red: "#ff3b3b",
  blueBg: "rgba(26,26,255,0.06)",
  redBg: "rgba(255,59,59,0.06)",
}

function makeChart(id, label1, label2, yLabel) {
  const ctx = document.getElementById(id)
  if (!ctx) return null
  return new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        { label: label1, data: [], borderColor: COLORS.blue, backgroundColor: COLORS.blueBg, borderWidth: 2, tension: 0, pointRadius: 4, pointStyle: "rectRot" },
        { label: label2, data: [], borderColor: COLORS.red,  backgroundColor: COLORS.redBg,  borderWidth: 2, tension: 0, pointRadius: 4, pointStyle: "rectRot" },
      ],
    },
    options: {
      animation: false,
      responsive: true,
      plugins: {
        legend: { position: "bottom", labels: { font: { family: "Space Grotesk", weight: "700" }, boxWidth: 12 } }
      },
      scales: {
        y: { title: { display: !!yLabel, text: yLabel || "", font: { family: "Space Grotesk", weight: "700" } }, grid: { color: "#e0d8cc" } },
        x: { title: { display: true, text: "Epoch", font: { family: "Space Grotesk", weight: "700" } }, grid: { color: "#e0d8cc" } },
      },
    },
  })
}

function updateChart(chart, labels, d1, d2) {
  if (!chart) return
  chart.data.labels = labels
  chart.data.datasets[0].data = d1
  chart.data.datasets[1].data = d2
  chart.update()
}

function destroyCharts() {
  Object.values(charts).forEach(c => c && c.destroy())
  charts = {}
}

async function initCharts() {
  await nextTick()
  destroyCharts()
  charts.accuracy = makeChart("chartAccuracy", "PyTorch", "TensorFlow", "Accuracy")
  charts.speed    = makeChart("chartSpeed",    "PyTorch", "TensorFlow", "Secondes")
  if (isAdmin.value) {
    charts.cpu = makeChart("chartCpu", "PyTorch", "TensorFlow", "%")
    charts.ram = makeChart("chartRam", "PyTorch", "TensorFlow", "Go")
  }
}

onMounted(async () => {
  const stored = localStorage.getItem("user")
  if (!stored) { router.push("/connexion"); return }
  user.value = JSON.parse(stored)
  await initCharts()
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
  destroyCharts()
})

const logout = () => {
  if (interval) clearInterval(interval)
  localStorage.removeItem("user")
  localStorage.removeItem("token")
  router.push("/connexion")
}

const startBenchmark = async () => {
  if (running.value) return
  const token = localStorage.getItem("token")
  if (!token) {
    router.push("/connexion")
    return
  }
  running.value = true
  message.value = "Lancement…"
  await initCharts()
  try {
    const res = await fetch("http://localhost:8000/prouteur/benchmark/start", {
      method: "POST",
      headers: { "Content-Type": "application/json",
                  "Authorization": `Bearer ${token}`
                },
      body: JSON.stringify({ dataset: dataset.value, epochs: 15 }),
    })
    if (res.status === 401) {
      logout() 
      return
    }
    const data = await res.json()
    jobId.value = data.job_id
    message.value = "Benchmark en cours…"
    interval = setInterval(updateStatus, 2000)
  } catch {
    message.value = "Serveur inaccessible"
    running.value = false
  }
}

const updateStatus = async () => {
  if (!jobId.value) return
  const token = localStorage.getItem("token")
  try {
    const res = await fetch(`http://localhost:8000/prouteur/benchmark/status/${jobId.value}`, {
      headers: { "Authorization": `Bearer ${token}` }
    })
    if (res.status === 401) {
      clearInterval(interval)
      logout()
      return
    }
    const data = await res.json()
    const pt = data.results?.pytorch?.history ?? []
    const tf = data.results?.tensorflow?.history ?? []
    const len = Math.max(pt.length, tf.length)
    const labels = Array.from({ length: len }, (_, i) => i + 1)

    updateChart(charts.accuracy, labels, pt.map(p => p.accuracy),    tf.map(p => p.accuracy))
    updateChart(charts.speed,    labels, pt.map(p => p.elapsed_time), tf.map(p => p.elapsed_time))
    if (isAdmin.value) {
      updateChart(charts.cpu, labels, pt.map(p => p.cpu_avg),    tf.map(p => p.cpu_avg))
      updateChart(charts.ram, labels, pt.map(p => p.ram_avg_gb), tf.map(p => p.ram_avg_gb))
    }

    if (data.status === "finished") {
      message.value = "Terminé!"
      clearInterval(interval)
      running.value = false
    } else if (data.status === "failed") {
      message.value = "Échoué: " + (data.error ?? "")
      clearInterval(interval)
      running.value = false
    }
  } catch { /* réessai */ }
}
</script>
