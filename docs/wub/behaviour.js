alert("hello")
document.addEventListener('alpine:init', () => {
    Alpine.store('darkMode', {
        on: false,

        toggle() {
            this.on = ! this.on
        }
    })
})
