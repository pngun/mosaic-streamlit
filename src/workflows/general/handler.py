import workflows.general.analysis as ann


class ImplementationError(Exception):
    def __init__(self, key, message=None, save=False):
        if message is None and save:
            message = f'"{key}" was not saved in the metadata. It must be of type {ArgumentsHandler.STORED_TYPES}'
        elif message is None:
            message = f'"{key}" was not initialized in the Arguments class.'
            message += " Please read the documents to understand the implementation requirements."
        super().__init__(message)


class EmptyAssay:
    def __init__(self):
        self.metadata = {}
        self.row_attrs = {}

    def add_metadata(self, key, val):
        self.metadata[key] = val

    def add_row_attr(self, key, val):
        self.row_attrs[key] = val


class ArgumentsHandler:
    """
    This class has is used to store the parameters
    in the h5 file
    """

    STORED_TYPES = (str, int, float, list)
    EXC_ATTR = ["get", "metakey", "save", "attributes"]

    def __init__(self, assaykey):
        self.assaykey = assaykey
        self._init_attrs = set()

        if f"_original_{self.assaykey}" not in dir(ann.data.sample):
            setattr(ann.data.sample, self.assaykey, EmptyAssay())
            setattr(ann.data.sample, f"_original_{self.assaykey}", EmptyAssay())
        else:
            ann.data.add_assay(self.assaykey)

        assay = getattr(ann.data.sample, f"_original_{self.assaykey}")

        # Initialize all variables with the defaults
        for key in dir(self):
            if not key.startswith("__") and key not in self.EXC_ATTR:
                val = getattr(self, key)
                self._init_attrs |= set(dir(self))
                if callable(val):
                    val()

        # Store variables in the h5 file
        # If already present use the stored value
        attributes = []
        for key in dir(self):
            if not key.startswith("__") and key not in self.EXC_ATTR:
                val = getattr(self, key)
                mkey = self.metakey(key)
                attributes.append(key)

                if isinstance(val, self.STORED_TYPES):
                    if mkey in assay.metadata:
                        try:
                            val = assay.metadata[mkey].item()
                        except ValueError:
                            val = list(assay.metadata[mkey])

                    assay.add_metadata(mkey, val)
                    self.__setattr__(key, val, overwrite=True)

        self.attributes = attributes + ["attributes", "_init_attrs"]

    def __setattr__(self, name, value, overwrite=False):
        """
        Check that the no new attributes are fetched

        Args:
            name: str
            value: str
            overwrite: bool

        Raises:
            ImplementationError: If attribute not initialized or duplicated
        """

        if "attributes" in dir(self):
            if name not in self.attributes:
                raise ImplementationError(name)
        elif "_init_attrs" in dir(self) and name in self._init_attrs and name != "_init_attrs" and not overwrite:
            message = f'"{name}" was used for two different argument names. Make sure each argument is unique.'
            message += f"Current value is {getattr(self, name)}, proposed value is {value}"
            raise ImplementationError(name, message)

        super().__setattr__(name, value)

    def __getattr__(self, name):
        """
        Check that the no new attributes are fetched

        Args:
            name: str

        Raises:
            ImplementationError: If attribute accessed without initialization
        """

        if "attributes" in dir(self) and name not in self.attributes:
            raise ImplementationError(name)

        super().__getattr__(name)

    def get(self, key):
        """
        Retrieve the value from the h5 file

        Args:
            key: str

        Returns:
            value of attribute

        Raises:
            ImplementationError: If attribute does not exist
        """

        if key not in self.attributes:
            raise ImplementationError(key)

        assay = getattr(ann.data.sample, f"_original_{self.assaykey}")
        mkey = self.metakey(key)

        if mkey not in assay.metadata:
            raise ImplementationError(key, save=True)

        val = assay.metadata[mkey]

        return val

    def metakey(self, key):
        """
        The key with which the data is to be stored
        in the assay metadata. This mapping is done
        to ensure unique keys and to prevent and
        overwritting of data.

        Args:
            key: str

        Returns:
            encoded string
        """

        return f"__mosaic_{self.assaykey}_{key}"

    def save(self):
        """
        Stores all the current arguments in the h5 file

        Raises:
            ImplementationError: If new attribute found
        """

        ogassay = getattr(ann.data.sample, f"_original_{self.assaykey}")
        assay = getattr(ann.data.sample, self.assaykey)
        for key in dir(self):
            if not key.startswith("__") and key not in self.EXC_ATTR:
                val = getattr(self, key)
                mkey = self.metakey(key)

                if key not in self.attributes:
                    raise ImplementationError(key)

                if isinstance(val, self.STORED_TYPES):
                    ogassay.add_metadata(mkey, val)
                    assay.add_metadata(mkey, val)

        for key in assay.metadata:
            ogassay.add_metadata(key, assay.metadata[key])

        for key in assay.row_attrs:
            ogassay.add_row_attr(key, assay.row_attrs[key])
