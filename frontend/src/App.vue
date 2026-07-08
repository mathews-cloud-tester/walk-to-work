<template>
  <div id="app">
    <header class="site-header">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">
          <Footprints :size="26" :stroke-width="2" />
        </div>
        <div class="brand-text">
          <p class="brand-name">Walk to Work</p>
          <p class="brand-tag">Commute tracker</p>
        </div>
      </div>
    </header>

    <main class="main-content">
      <WalkTracker />
    </main>

    <footer class="site-footer">
      <p>Track your walking commute — distance, time, and streak</p>
    </footer>
  </div>
</template>

<script>
import { Footprints } from 'lucide-vue-next'
import WalkTracker from './components/WalkTracker.vue'

export default {
  name: 'App',
  components: {
    Footprints,
    WalkTracker
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
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
}

#app {
  min-height: 100vh;
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
}

.brand {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
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
  color: var(--text-light);
  font-size: 0.875rem;
  border-top: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.6);
}

@media (max-width: 640px) {
  .brand {
    padding: 0.85rem 1rem;
  }

  .main-content {
    padding: 1.25rem 1rem 2rem;
  }
}
</style>
