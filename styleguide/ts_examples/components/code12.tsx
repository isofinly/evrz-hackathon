import React, { useState, useEffect } from "react";
import styles from "./BadComponent.module.css";

const MonolithicComponent = () => {
  const [users, setUsers] = useState([]);
  const [posts, setPosts] = useState([]);
  const [comments, setComments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [filterType, setFilterType] = useState("all");

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    if (selectedUser) {
      fetchUserPosts();
    }
  }, [selectedUser]);

  useEffect(() => {
    if (posts.length) {
      fetchComments();
    }
  }, [posts]);

  const fetchUsers = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("https://api.example.com/users");
      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    }
    setIsLoading(false);
  };

  const fetchUserPosts = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `https://api.example.com/posts?userId=${selectedUser}`
      );
      const data = await response.json();
      setPosts(data);
    } catch (err) {
      setError(err.message);
    }
    setIsLoading(false);
  };

  const fetchComments = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`https://api.example.com/comments`);
      const data = await response.json();
      setComments(data);
    } catch (err) {
      setError(err.message);
    }
    setIsLoading(false);
  };

  const handleUserSelect = (userId) => {
    setSelectedUser(userId);
  };

  const handleFilterChange = (type) => {
    setFilterType(type);
  };

  const filterPosts = () => {
    if (filterType === "all") return posts;
    return posts.filter((post) => post.type === filterType);
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className={styles.container}>
      <div>
        <h2>Select User</h2>
        {users.map((user) => (
          <button key={user.id} onClick={() => handleUserSelect(user.id)}>
            {user.name}
          </button>
        ))}
      </div>

      <div>
        <h2>Filter Posts</h2>
        <select onChange={(e) => handleFilterChange(e.target.value)}>
          <option value="all">All Posts</option>
          <option value="news">News</option>
          <option value="blog">Blog</option>
        </select>
      </div>

      <div>
        <h2>Posts</h2>
        {filterPosts().map((post) => (
          <div key={post.id} className={styles.card}>
            <h3>{post.title}</h3>
            <p>{post.content}</p>
            <div>
              <h4>Comments</h4>
              {comments
                .filter((comment) => comment.postId === post.id)
                .map((comment) => (
                  <div key={comment.id}>
                    <p>{comment.text}</p>
                    <small>{comment.author}</small>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MonolithicComponent;
