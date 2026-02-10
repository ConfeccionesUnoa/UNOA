import { defineAbility } from '@casl/ability'

const ability = defineAbility((can,) => { // cannot (no lo uso aún)
  can(
    ['create', 'read', 'update', 'delete', 'detail', 'finish'],
    ['Usuarios', 'Inventario', 'Programacion']
  )
})

export default ability
export { ability }