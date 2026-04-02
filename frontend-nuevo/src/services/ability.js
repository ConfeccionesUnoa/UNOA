import { defineAbility } from '@casl/ability'

const ability = defineAbility(() => {
  // permisos abiertos por rol se configuran en LoginPage y MainLayout con ability.update(rules)
})

export default ability
export { ability }