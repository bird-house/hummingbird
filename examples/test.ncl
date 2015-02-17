; Test the read_colormap_file function.
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"

begin

  cmap = read_colormap_file("BlAqGrYeOrReVi200")
  print(cmap)

end
