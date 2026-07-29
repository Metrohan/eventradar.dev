import React from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery } from 'react-query'
import ReactMarkdown from 'react-markdown'

import LoadingSpinner from '../components/LoadingSpinner'
import { publicAPI } from '../services/api'
import { setPageSEO } from '../utils/seo'

const BlogDetailPage = () => {
  const { slug } = useParams()
  const { data, isLoading, error } = useQuery(['blog-post', slug], () => publicAPI.getBlogPost(slug), { retry: false })
  const post = data?.data

  React.useEffect(() => {
    if (!post) return

    setPageSEO({ title: `${post.title} | TechEventRadar`, description: post.summary, path: `/blog/${post.slug}` })

    const schema = {
      '@context': 'https://schema.org',
      '@type': 'BlogPosting',
      headline: post.title,
      description: post.summary,
      image: 'https://eventradar.dev/banner.png',
      datePublished: post.published_at,
      author: { '@type': 'Organization', name: 'TechEventRadar' },
      publisher: { '@type': 'Organization', name: 'TechEventRadar' },
      mainEntityOfPage: `https://eventradar.dev/blog/${post.slug}`,
    }
    document.getElementById('blog-jsonld')?.remove()
    const script = document.createElement('script')
    script.id = 'blog-jsonld'
    script.type = 'application/ld+json'
    script.text = JSON.stringify(schema)
      .replace(/</g, '\\u003c')
      .replace(/>/g, '\\u003e')
      .replace(/&/g, '\\u0026')
      .replace(/\u2028/g, '\\u2028')
      .replace(/\u2029/g, '\\u2029')
    document.head.appendChild(script)

    return () => {
      document.getElementById('blog-jsonld')?.remove()
    }
  }, [post])

  if (isLoading) return <LoadingSpinner />
  if (error || !post) return <div className="container py-5"><h1>Yazı bulunamadı</h1><Link to="/blog">Bloga dön</Link></div>

  return (
    <article className="container py-5" style={{ maxWidth: 820 }}>
      <Link to="/blog" style={{ color: 'var(--action-primary)', textDecoration: 'none' }}>← Tüm yazılar</Link>
      <h1 style={{ color: 'var(--text-primary)', fontWeight: 800, marginTop: '1rem' }}>{post.title}</h1>
      <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem' }}>{post.summary}</p>
      <div style={{ borderTop: '1px solid var(--border-color)', marginTop: '1.5rem', paddingTop: '1.5rem', color: 'var(--text-primary)', lineHeight: 1.75 }}>
        <ReactMarkdown components={{ a: props => <a {...props} target="_blank" rel="noopener noreferrer" /> }}>{post.content}</ReactMarkdown>
      </div>
    </article>
  )
}

export default BlogDetailPage
