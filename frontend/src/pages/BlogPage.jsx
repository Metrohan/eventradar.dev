import React from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from 'react-query'
import { useTranslation } from 'react-i18next'
import { format } from 'date-fns'

import LoadingSpinner from '../components/LoadingSpinner'
import { publicAPI } from '../services/api'
import { setPageSEO } from '../utils/seo'
import { useDateLocale } from '../hooks/useDateLocale'

const BlogPage = () => {
  const { t, i18n } = useTranslation()
  const dateLocale = useDateLocale()

  React.useEffect(() => {
    setPageSEO({
      title: 'Haftalık Teknoloji Etkinlikleri | TechEventRadar',
      tabTitle: `${t('blog.title')} | TechEventRadar`,
      description: 'Her hafta öne çıkan hackathon, bootcamp, seminer ve teknoloji etkinliklerini keşfet.',
      path: '/blog',
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language])

  const { data, isLoading, error } = useQuery('blog-posts', publicAPI.getBlogPosts)
  const posts = data?.data?.posts || []

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="container py-5" style={{ maxWidth: 900 }}>
      <h1 style={{ color: 'var(--text-primary)', fontWeight: 800 }}>{t('blog.title')}</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        {t('blog.subtitle')}
      </p>
      {error && <p style={{ color: 'var(--danger)' }}>{t('blog.loadError')}</p>}
      {!error && posts.length === 0 && <p style={{ color: 'var(--text-muted)' }}>{t('blog.comingSoon')}</p>}
      <div style={{ display: 'grid', gap: '1rem' }}>
        {posts.map(post => (
          <Link
            key={post.id}
            to={`/blog/${post.slug}`}
            style={{ display: 'block', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 14, padding: '1.5rem', color: 'inherit', textDecoration: 'none' }}
          >
            <time style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              {format(new Date(post.published_at), 'dd MMMM yyyy', { locale: dateLocale })}
            </time>
            <h2 style={{ fontSize: '1.25rem', margin: '0.5rem 0', color: 'var(--text-primary)' }}>
              {post.title}
            </h2>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>{post.summary}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default BlogPage
