function updateObject(oldObject: object, updatedProperties: object): object {
  return Object.assign({}, oldObject, updatedProperties);
}

export default updateObject;
