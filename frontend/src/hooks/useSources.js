import { useQuery } from 'react-query'
import { publicAPI } from '../services/api'

const useSources = () => {
  const query = useQuery('sources', publicAPI.getSources, {
    staleTime: Infinity,
    retry: 2,
  })

  return {
    ...query,
    sources: query.data?.data || [],
  }
}

export default useSources
