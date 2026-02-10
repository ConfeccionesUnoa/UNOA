export default async () => {
  if (process.env.NODE_ENV === 'development' && 'serviceWorker' in navigator) {
    try {
      const regs = await navigator.serviceWorker.getRegistrations()
      for (const reg of regs) {
        try {
          await reg.unregister()
          /* eslint-disable no-console */
          console.info('Service worker unregistered (dev):', reg.scope)
        } catch (err) {
          console.warn('Failed to unregister service worker', err)
        }
      }
    } catch (err) {
      console.warn('Error when attempting to get service worker registrations', err)
    }
  }
}
