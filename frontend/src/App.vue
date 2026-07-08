<template>
  <div id="app">
    <header class="site-header">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">
          <Footprints :size="26" :stroke-width="2" />
        </div>
        <div class="brand-text">
          <p class="brand-name">Walk to Work</p>
          <p class="brand-tag">{{ subtitle }}</p>
        </div>
      </div>
      <button
        v-if="deferredPrompt"
        type="button"
        class="install-btn"
        @click="installApp"
      >
        Install
      </button>
    </header>

    <main class="main-content">
      <WalkTracker />
    </main>

    <footer class="site-footer">
      <p>{{ footerText }}</p>
    </footer>
  </div>
</template>

<script>
import { Footprints } from 'lucide-vue-next'
import WalkTracker from './components/WalkTracker.vue'
import { isOfflineFirst } from './services/api.js'

export default {
  name: 'App',
  components: {
    Footprints,
    WalkTracker
  },
  data() {
    return {
      deferredPrompt: null,
      installed: false,
      isNative: false
    }
  },
  computed: {
    subtitle() {
      if (this.isNative) return 'On your phone'
      if (isOfflineFirst) return 'Works offline on your device'
      return 'Commute tracker'
    },
    footerText() {
      if (isOfflineFirst) return 'Walks are saved on this device'
      return 'Track your walking commute — distance, time, and streak'
    }
  },
  mounted() {
    this.isNative = !!(window.Capacitor?.isNativePlatform?.())
    window.addEventListener('beforeinstallprompt', this.onInstallPrompt)
    window.addEventListener('appinstalled', this.onInstalled)
  },
  beforeUnmount() {
    window.removeEventListener('beforeinstallprompt', this.onInstallPrompt)
    window.removeEventListener('appinstalled', this.onInstalled)
  },
  methods: {
    onInstallPrompt(e) {
      e.preventDefault()
      this.deferredPrompt = e
    },
    onInstalled() {
      this.installed = true
      this.deferredPrompt = null
    },
    async installApp() {
      if (!this.deferredPrompt) return
      this.deferredPrompt.prompt()
      await this.deferredPrompt.userChoice
      this.deferredPrompt = null
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  -webkit-tap-highlight-color: transparent;
}

:root {
  --primary: #0f766e;
  --primary-dark: #0d5f59;
  --primary-light: #ccfbf1;
  --accent: #c2410c;
  --bg-light: #f4f7f6;
  --bg-white: #ffffff;
  --bg-cream: #e8efed;
  --text-dark: #14201e;
  --text-gray: #3d4f4b;
  --text-light: #6b7f7a;
  --border: #d5e0dd;
  --shadow: 0 1px 3px rgba(20, 32, 30, 0.08);
  --shadow-md: 0 4px 12px rgba(20, 32, 30, 0.08);
  --shadow-lg: 0 12px 28px rgba(20, 32, 30, 0.1);
  --safe-top: env(safe-area-inset-top, 0px);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
}

html, body {
  overscroll-behavior-y: none;
}

body {
  font-family: 'DM Sans', system-ui, sans-serif;
  background:
    radial-gradient(ellipse 80% 50% at 10% -10%, rgba(15, 118, 110, 0.12), transparent 55%),
    radial-gradient(ellipse 60% 40% at 100% 0%, rgba(194, 65, 12, 0.08), transparent 50%),
    linear-gradient(180deg, #f7faf9 0%, var(--bg-light) 40%, #eef3f1 100%);
  color: var(--text-dark);
  line-height: 1.6;
  min-height: 100vh;
  min-height: 100dvh;
}

#app {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.85);
  border-bottom: 1px solid var(--border);
  padding-top: var(--safe-top);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.brand {
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.site-header .brand {
  margin: 0;
  flex: 1;
}

.install-btn {
  margin-right: 1rem;
  border: none;
  background: var(--primary);
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.55rem 0.9rem;
  border-radius: 999px;
  cursor: pointer;
  flex-shrink: 0;
}

.brand-mark {
  width: 48px;
  height: 48px;
  border-radius: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, var(--primary-light), #99f6e4);
  color: var(--primary);
  box-shadow: var(--shadow);
}

.brand-name {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--text-dark);
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.brand-tag {
  font-size: 0.8rem;
  color: var(--text-light);
  font-weight: 500;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 1.75rem 1.5rem 2.5rem;
}

.site-footer {
  text-align: center;
  padding: 1.25rem;
  padding-bottom: calc(1.25rem + var(--safe-bottom));
  color: var(--text-light);
  font-size: 0.875rem;
  border-top: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.6);
}

@media (max-width: 640px) {
  .brand {
    padding: 0.85rem 1rem;
  }

  .install-btn {
    margin-right: 0.75rem;
  }

  .main-content {
    padding: 1.25rem 1rem 2rem;
  }

  .brand-name {
    font-size: 1.25rem;
  }
}
</style>
