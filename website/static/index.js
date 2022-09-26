function like(postId) {
    const likeCount = document.getElementById(`likes-count-${postId}`);
    const likeButton = document.getElementById(`like-button-${postId}`);
  
    fetch(`/like-post/${postId}`, { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        likeCount.innerHTML = data["likes"];
        if (data["liked"] === true) {
          likeButton.className = "fas fa-thumbs-up";
        } else {
          likeButton.className = "far fa-thumbs-up";
        }
      })
      .catch((e) => alert("Could not like post."));
  }


  function follow(userId) {
    const likeCount = document.getElementById(`follows-count-${postId}`);
    const likeButton = document.getElementById(`follows-button-${postId}`);
  
    fetch(`/follow/channel/${userId}`, { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        likeCount.innerHTML = data["channels"];
        if (data["channels"] === true) {
          likeButton.className = "fas fa-thumbs-up";
        } else {
          likeButton.className = "far fa-thumbs-up";
        }
      })
      .catch((e) => alert("Could not like post."));
  }



function gotoprofile() {
  window.location.href = `/upload-image`;

}



function gotoprofile(username) {
    window.location.href = `/profile/${username}`;

}


function follow(username) {
    fetch(`/follow/${username}`, { method: "POST" })
}



