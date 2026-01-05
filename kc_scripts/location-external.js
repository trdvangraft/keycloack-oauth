var identity = $evaluation.getContext().getIdentity();
var attrs = identity.getAttributes();

var locAttr = attrs.getValue('location');
var loc = locAttr ? locAttr.asString(0) : null;

if (loc === 'external') {
  $evaluation.grant();
}
