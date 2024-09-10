import React from 'react';

import LoadingAnimation from './LoadingAnimation'

const Loading = ({children, errors = [], loading = true, content = <></>}) => {
  // find first error that is not undefined or null
  const error = errors.find((error) => error !== undefined && error !== null)
  if (error) {
    return <LoadingAnimation content={error.message} failed={error.isGeneric}/>
  }
  if (loading) {
    return (
      <LoadingAnimation content={content} failed={false}/>
    )
  }
  return children
}
export default Loading
