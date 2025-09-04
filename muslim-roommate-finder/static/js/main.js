document.addEventListener("DOMContentLoaded", () => {
    const deleteButtons = document.querySelectorAll(".delete-btn");
    
    deleteButtons.forEach(btn => {
      btn.addEventListener("click", (e) => {
        if (!confirm("Are you sure you want to delete this item?")) {
          e.preventDefault();
        }
      });
    });
  });
  