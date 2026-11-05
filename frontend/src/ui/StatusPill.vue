<template><span class="status-pill" :class="status"><i></i>{{ label || (asset ? assetStates[status] : requestStates[status]) || status }}</span></template>
<script setup>
import { requestStates, assetStates } from '../utils/format'
defineProps({ status: String, label: String, asset: Boolean })
</script>
