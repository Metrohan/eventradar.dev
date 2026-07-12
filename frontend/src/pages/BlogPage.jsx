import React from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from 'react-query'

import LoadingSpinner from '../components/LoadingSpinner'
import { publicAPI } from '../services/api'
import { setPageSEO } from '../utils/seo'

const BlogPage = () => {
  React.useEffect(() => {
    setPageSEO({
      title: 'Haftalık Teknoloji Etkinlikleri | TechEventRadar',
      description: 'Her hafta öne çıkan hackathon, bootcamp, seminer ve teknoloji etkinliklerini keşfet.',
      path: '/blog',
    })
  }, [])

  const { data, isLoading, error } = useQuery('blog-posts', publicAPI.getBlogPosts)
  const posts = data?.data?.posts || []

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="container py-5" style={{ maxWidth: 900 }}>
      <h1 style={{ color: 'var(--text-primary)', fontWeight: 800 }}>Haftalık Etkinlik Rehberi</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Önümüzdeki haftanın teknoloji etkinliklerini kısa ve güncel özetlerle takip et.
      </p>
      {error && <p style={{ color: 'var(--danger)' }}>Blog yazıları yüklenemedi.</p>}
      {!error && posts.length === 0 && <p style={{ color: 'var(--text-muted)' }}>İlk haftalık rehber yakında burada.</p>}
      <div style={{ display: 'grid', gap: '1rem' }}>
        {posts.map(post => (
          <article key={post.id} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 14, padding: '1.5rem' }}>
            <time style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              {new Date(post.published_at).toLocaleDateString('tr-TR')}
            </time>
            <h2 style={{ fontSize: '1.25rem', margin: '0.5rem 0', color: 'var(--text-primary)' }}>
              <Link to={`/blog/${post.slug}`} style={{ color: 'inherit', textDecoration: 'none' }}>{post.title}</Link>
            </h2>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>{post.summary}</p>
          </article>
        ))}
      </div>
    </div>
  )
}

export default BlogPage
