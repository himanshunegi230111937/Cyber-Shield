document.addEventListener("DOMContentLoaded", () => {
  const passwordInput = document.getElementById("password");
  if (passwordInput) {
    passwordInput.addEventListener("input", async () => {
      const res = await fetch("/check-strength", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: passwordInput.value })
      });
      const data = await res.json();
      document.getElementById("strength-result").innerText = `Strength: ${data.strength}`;
      document.getElementById("remarks").innerText = `Suggestions:\n${data.remarks.join('\n')}`;
      updateBar(data.score);
    });
  }
});

function updateBar(score) {
  const bar = document.getElementById("strength-bar");
  const colors = ["#ff0000", "#ff6600", "#ffcc00", "#99cc00", "#33cc33", "#009900"];
  bar.style.width = `${(score / 5) * 100}%`;
  bar.style.backgroundColor = colors[score];
}

// Add loader CSS class dynamically if not present
if (!document.getElementById('dynamic-loader-style')) {
  const style = document.createElement('style');
  style.id = 'dynamic-loader-style';
  style.innerHTML = `
  .loader {
    border: 6px solid #f3f3f3;
    border-top: 6px solid #0077b6;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    animation: spin 1s linear infinite;
    display: inline-block;
    vertical-align: middle;
    margin-right: 8px;
  }
  @keyframes spin {
    0% { transform: rotate(0deg);}
    100% { transform: rotate(360deg);}
  }`;
  document.head.appendChild(style);
}

async function crackPassword() {
  const pwd = document.getElementById("crack-password").value;
  const isHash = document.getElementById("toggle-hash").checked ? "true" : "false";
  const fileInput = document.getElementById("dictionary-file");
  const attackType = document.getElementById("attack-type").value;
  const resultElem = document.getElementById("result");
  const detailsElem = document.getElementById("crack-details");
  const timeElem = document.getElementById("time-taken");
  const attemptsElem = document.getElementById("attempts");
  const strengthElem = document.getElementById("strength-percent");
  const suggestionElem = document.getElementById("suggestion");
  const processing = document.getElementById("processing");

  const maxLength = document.getElementById("max-length") ? document.getElementById("max-length").value : 4;
  formData.append("maxLength", maxLength);

  if (fileInput.files.length > 0) {
    formData.append("dictionary", fileInput.files[0]);
  }

  let formData = new FormData();
  formData.append("input", pwd);
  formData.append("isHash", isHash ? "true" : "false");
  formData.append("attackType", attackType);
  if (fileInput && fileInput.files.length > 0) {
    formData.append("dictionary", fileInput.files[0]);
  }

  resultElem.innerText = "";
  detailsElem.style.display = "none";
  processing.style.display = "block";

  const hashType = document.getElementById("hash-type") ? document.getElementById("hash-type").value : "md5";
  formData.append("hashType", hashType);

  const res = await fetch("/password_cracker", {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  processing.style.display = "none";
  if (data.found) {
    resultElem.innerHTML = `<b>Password found!</b> <br>Value: <code>${data.password}</code>`;
  } else {
    resultElem.innerText = "Password not found!";
  }
  timeElem.innerText = data.time_taken;
  attemptsElem.innerText = data.attempts;
  strengthElem.innerText = data.strength_percent;
  suggestionElem.innerText = data.suggestion;
  detailsElem.style.display = "block";
}

function toggleDropdown() {
  document.getElementById("dropdownMenu").classList.toggle("show");
}
window.onclick = function (event) {
  if (!event.target.matches('.dropbtn')) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    for (var i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}